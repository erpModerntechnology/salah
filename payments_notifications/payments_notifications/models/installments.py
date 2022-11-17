from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta ,date
from dateutil.relativedelta import relativedelta
from datetime import datetime


class AccountPaymentRegisterInstallment(models.TransientModel):
    _inherit = 'account.payment.register'
    notification_bill = fields.Many2one(
        'account.notification',
    )
    bill = fields.Many2one(
        'account.move',
        compute='_compute_bill'
    )
    def _compute_bill(self):
        for rec in self:
            if rec.communication:
                account_move = self.env['account.move'].search([('name','=',rec.communication)])
                rec.bill = account_move.id
            else:
                rec.bill=None

    @api.onchange('notification_bill')
    def onchange_notification_bill(self):
        self.amount = self.notification_bill.amount


    def action_create_payments(self):
        self.notification_bill.paid = True
        print(self.bill.invoice_date if self.bill.invoice_date else date.today())
        print(self.bill.inst_debit_account_id.id)
        print(self.bill.inst_credit_account_id.id)
        payments = self._create_payments()
        print(payments)
        entry = self.env['account.move'].create({
            'move_type': 'entry',
            'date':self.bill.invoice_date if self.bill.invoice_date else date.today(),

            'line_ids': [
                (0, 0, {
                    'name': 'line_debit',
                    'account_id': self.bill.inst_debit_account_id.id,
                    'debit': (self.bill.won_percen / 100) * self.notification_bill.amount
                }),
                (0, 0, {
                    'name': 'line_credit',
                    'account_id': self.bill.inst_credit_account_id.id,
                    'credit': (self.bill.won_percen / 100) * self.notification_bill.amount
                }),
            ],
        })
        self.notification_bill.ins_journal_id = entry.id
        self.notification_bill.ins_journal_id.action_post()



        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action

class installmentReport(models.TransientModel):
    _name = 'installment.report'
    _description = 'Installment report'
    dof3a = fields.Selection(
        string='الدفعه',
        selection=[
            ('الدفعه الاولي', 'الدفعه الاولي'),
            ('الدفعه الثانيه', 'الدفعه الثانيه'),
            ('الدفعه الثالثه', 'الدفعه الثالثه'),
            ('الدفعه الرابعه', 'الدفعه الرابعه'),
            ('الدفعه الخامسه', 'الدفعه الخامسه'),
            ('الدفعه السادسه', 'الدفعه السادسه'),
            ('الدفعه السابعه', 'الدفعه السابعه'),
            ('الدفعه الثامنه', 'الدفعه الثامنه'),
            ('الدفعه التاسعه', 'الدفعه التاسعه'),
            ('الدفعه العاشره', 'الدفعه العاشره'),
            ('الدفعه الحاديه عشر', 'الدفعه الحاديه عشر'),
            ('الدفعه الثانيه عشر', 'الدفعه الثانيه عشر'),
            ('الدفعه الثالثه عشر', 'الدفعه الثالثه عشر'),
            ('الدفعه الرابعه عشر', 'الدفعه الرابعه عشر'),
            ('الدفعه الخامسه عشر', 'الدفعه الخامسه عشر'),
            ('الدفعه السادسه عشر', 'الدفعه السادسه عشر'),
            ('الدفعه السابعه عشر', 'الدفعه السابعه عشر'),
            ('الدفعه الثامنه عشر', 'الدفعه الثامنه عشر'),
            ('الدفعه التساعه عشر', 'الدفعه التساعه عشر'),
            ('الدفعه العشرون', 'الدفعه العشرون'), ],
        required=False, )
    partner_id = fields.Many2many('res.partner', string='Partner', required=False)
    all_customer = fields.Boolean(
        string='All Customer',
        required=False,default=True)

    def days_between(self,d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)
    def print_report(self):
            domain = []
            print(self.dof3a)
            if self.dof3a:
                d= (('dof3a','=',self.dof3a))
                domain.append(d)
                d= (('date','<=', date.today()))
                domain.append(d)
                d= (('paid','!=',True))
                domain.append(d)
                    
                    
                print(domain)
            datas = []
            if self.partner_id and not self.all_customer:
                domain.append(('partner_id', 'in', self.partner_id.ids))
                account_notification = self.env['account.notification'].search(domain)
                print(account_notification)
            elif self.all_customer:
                account_notification = self.env['account.notification'].search([])

            for rec in account_notification:
                print(account_notification)
                print(rec.date ,datetime.today().date())
                if rec.date < datetime.today().date() and not rec.paid:
                   print(rec.date)
                   diff = datetime.today().date() - rec.date
                   datas.append({
                        'name': rec.partner_id.name,
                        'date': rec.date,
                        'diff': diff.days,
                        'amount': round(rec.amount,2),
                    })
            res = {
                'attendances': datas,

            }
            data = {
                'form': res,
            }
            print(data)

            return self.env.ref('payments_notifications.report_installment1').report_action([], data=data)


class installmentWizard(models.TransientModel):
    _name = 'installment.wizard'

    _description = 'Installment Wizard'


    no_of_months = fields.Integer(
        string='No of Months',
        required=False)
    start_date = fields.Date(
        string='Start date ',
        required=False)
    def make_installment(self):
        self.invoice_id.notification_bill = None
        ll =[]
        to_19_ar = ( u'الدفعه الاولي', u'الدفعه الثانيه', u'الدفعه الثالثه', u'الدفعه الرابعه', u'الدفعه الخامسه',
                     u'الدفعه السادسه',
                    u'الدفعه السابعه', u'الدفعه الثامنه', u'الدفعه التاسعه', u'الدفعه العاشره', u'الدفعه الحاديه عشر', u'الدفعه الثانيه عشر', u'الدفعه الثالثه عشر',
                    u'الدفعه الرابعه عشر', u'الدفعه الخامسه عشر', u'الدفعه السادسه عشر', u'الدفعه السابعه عشر', u'الدفعه الثامنه عشر', u'الدفعه التساعه عشر', u'الدفعه العشرون')
        for i in range(0,self.no_of_months):

            row= (0, 0, {
                'date': self.start_date +  relativedelta(months =i),
                'amount': self.invoice_id.amount_residual/self.no_of_months,
                'dof3a' : to_19_ar[i]
            })


            ll.append(row)

        self.invoice_id.notification_bill = ll
        print(ll)
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        required=False)


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    bill = fields.Many2one(
        'account.move',
    )

    notification_bill = fields.Many2one(
        'account.notification',
    )

    def post(self):
        if self.notification_bill:
            paid = self.env['account.notification'].search([('id', '=', self.notification_bill.id)])
            paid.paid = True
        else:
            self.env['account.notification'].sudo().create({
                'notification': self.bill.id,
                'date': date.today(),
                'paid': True,
                'channel': None,
                'amount': self.amount,
            })
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(
                        lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (
                                line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label)) \
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids') \
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
                    .reconcile()

        return True

    @api.onchange('notification_bill')
    def _get_amount(self):
        if self.notification_bill:
            bill = self.notification_bill.id
            cash = self.env['account.notification'].search([('id', '=', bill)])
            self.amount = cash.amount


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'
    def _get_default_debit(self):
        account_dibit =self.env['account.account'].search([('code','=','1110001')])
        if account_dibit:
            return account_dibit.id
        else:
            return False
    def _get_default_credit_account(self):
        account_credit =self.env['account.account'].search([('code','=','1111000')])
        if account_credit:
            return account_credit.id
        else:
            return False
    inst_debit_account_id = fields.Many2one('account.account', string='Depit Account',default=_get_default_debit)
    inst_credit_account_id = fields.Many2one('account.account', string='Depit Account',default=_get_default_credit_account)
    journal_entry_id = fields.Many2one('account.move', )
    won_percen = fields.Float("نسبة الفائده")

    notification_bill = fields.One2many(
        'account.notification',
        'notification'
    )
    channel = fields.Many2one(
        'mail.channel',
        domain=[('channel_type', '=', 'channel')],
    )
    installments_total = fields.Float(
        compute='_compute_installments',
    )
    remaining = fields.Float(
        compute='_compute_remaining'
    )

    def action_post(self):
        res = super(AccountInvoiceInherit, self).action_post()
        
        if  self :
            if self.move_type != 'entry':

                entry = self.env['account.move'].create({
                    'move_type': 'entry',
                    'date': self.invoice_date if self.invoice_date else date.today(),
                    'line_ids': [
                        (0, 0, {
                            'name': 'line_debit',
                            'account_id': self.inst_debit_account_id.id,
                            'debit':(self.won_percen/100)*self.amount_total
                        }),
                        (0, 0, {
                            'name': 'line_credit',
                            'account_id': self.inst_credit_account_id.id,
                            'credit': (self.won_percen / 100) * self.amount_total
                        }),
                    ],
                })
                self.journal_entry_id = entry.id

                self.journal_entry_id.action_post()
        return res

    def _compute_installments(self):
        for rec in self:
            total = 0
            cashes = self.env['account.notification'].search([('notification', '=', rec.id)])
            for cash in cashes:
                total = total + cash.amount
            rec.installments_total = total

    def _compute_remaining(self):
        for rec in self:
            remain = rec.amount_total - rec.installments_total
            rec.remaining = remain

    @api.onchange('channel')
    def _channels(self):
        bill = self._origin.id
        dates = self.env['account.notification'].search([('notification', '=', bill)])
        for data in dates:
            data.channel = self.channel

    @api.constrains('notification_bill')
    def _max_notification_bill(self):
        for rec in self:
            total = 0
            cashes = self.env['account.notification'].search([('notification', '=', self.id)])
            for cash in cashes:
                total = total + cash.amount
            if total > rec.amount_total:
                raise ValidationError('Installments Total is more than the invoice Total.')


class Notification(models.Model):
    _name = "account.notification"
    _description = "Account Installments And Notifications"


    name = fields.Char(
        string='Name',
        compute='_compute_name',
    )
    notification = fields.Many2one(
        comodel_name='account.move',
        ondelete="cascade"
    )
    ins_journal_id = fields.Many2one('account.move')
    dof3a = fields.Char(
        string='الدفعه',
        required=False)
    date = fields.Date(
        required=True
    )
    partner_id = fields.Many2one(related='notification.partner_id', string="partner")


    paid = fields.Boolean()
    amount = fields.Float()
    channel = fields.Many2one('mail.channel')

    def _compute_name(self):
        for rec in self:
            rec.name = str(rec.date.strftime('%d-%m-%Y'))

    def vendor_notification(self):
        dates = self.env['account.notification'].search([('date', '<=', date.today()), ('paid', '!=', True)])
        for data in dates:
            if data.channel:
                body = 'Please be informed that the (invoice/bill) ' + data.notification.name + ' has a due payment on date ' + data.date.strftime(
                    '%d-%m-%Y') + ' With the amount ' + str(data.amount)
                data.channel.message_post(body=body, subtype_id=self.env.ref('mail.mt_note').id, author_id=2)
                print( data.channel.message_post(body=body, subtype_id=self.env.ref('mail.mt_note').id, author_id=2))

